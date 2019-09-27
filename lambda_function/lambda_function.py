def lambda_handler(event, context):
	import boto3
	import datetime

	## Get current utc time(hour)
	utcnowHour = datetime.datetime.utcnow()
	nowHour = int((str(utcnowHour.hour) + str(utcnowHour.minute))[:2])

	## Iterate through all aws regions
	ec2 = boto3.client('ec2', region_name="us-west-1")
	regions = ec2.describe_regions()
	for region in regions["Regions"]:
		regionName = region["RegionName"]

		## Get instance tag data
		client = boto3.client('ec2', regionName)
		ec2 = boto3.resource('ec2',  regionName)
		response = client.describe_tags(
			Filters=[
				{
					'Name': 'resource-type',
					'Values': [
						'instance'
					]
				}
			]
		)

		## Get the tag with Key "TIME" and extract Start and Stop time from the value(hour)
		for tags in response["Tags"]:
			if tags["Key"] == "TIME":
				time = tags["Value"].split("/")
				stopHour = int(time[0][:2])
				startHour = int(time[-1][:2])
				instance = ec2.Instance(tags['ResourceId'])
				try:
					##Stop an instance if stop time equals current utc time
					if stopHour == nowHour:
						print("stopping", tags['ResourceId'], regionName)
						instance.stop()
					##Start an instance if start time equals current utc time
					if startHour == nowHour:
						print("starting", tags['ResourceId'], regionName)
						instance.start()
				except ValueError:
					pass