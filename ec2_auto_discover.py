
from boto.utils import get_instance_metadata
import boto.ec2.autoscale

def get_current_region():
    metadata = get_instance_metadata()
    zone = metadata['placement']['availability-zone']
    return zone[:-1]
    
def get_current_vpc():
    metadata = get_instance_metadata()
    return metadata['network']['interfaces']['macs'].items()[0][1]['vpc-id']
    
def get_instances(tag_name=None, tag_value=None):
    ec2 = boto.ec2.connect_to_region(get_current_region())
    autoscale = boto.ec2.autoscale.connect_to_region(get_current_region())
    
    if tag_name:
        filter={'tag:' + tag_name: tag_value, 'vpc-id': get_current_vpc()}
    else:
        filter={'vpc-id': get_current_vpc()}
    
    instances = [];
    
    try:
        for res in ec2.get_all_instances(filters=filter):
            for instance in res.instances:
                as_instances = autoscale.get_all_autoscaling_instances(instance_ids=[instance.id])
            
                if(len(as_instances) == 1):
                    # instance is part of autoscale group - only add if lifecycle state is 'InService'
                    if(as_instances[0].lifecycle_state == 'InService'):
                        instances.append(instance)
                else:
                    # not an autoscaled instance - just add to list
                    instances.append(instance)
    finally:
        ec2.close()
        autoscale.close()
    
    return instances        
