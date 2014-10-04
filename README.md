#haproxy-ec2-auto-discover

##Description
When running applications on Amazon Web Services it is best to provision a load balancer / reverse proxy in front of the 
instances to provide an additional level of protection and enable the ability to achieve advanced configuration like 
offloading SSL processing and replacing instances in service with minimal disruption.

Best practise dictates running application server instance in private subnets in VPC and using auto-scaling to provide redundancy by 
automatically replacing faulty instances. Trouble with this approach is that manual effort is required to add / remove 
backend instances within the HAProxy configuration.

Enter haproxy-ec2-auto-discover. A python script that can automatically detect instances within a VPC and update the 
HAProxy configuration on the fly. Optionally tags can be used to filter out instances that are discovered.

Inspired from [https://github.com/markcaudill/haproxy-autoscale](https://github.com/markcaudill/haproxy-autoscale)

##Requirements
* haproxy >= 1.5-dev19
* python >= 2.7
* boto >= 2.27
* mako >= 0.5.0
* argeparse >= 1.2.1

##Configuration
A sample HAProxy configuration template is provided in template/haproxy.template. 

Customize these templates to fit your needs as you desire. 
##Using
haproxy-ec2-auto-discover is designed to be run on the HAProxy instance from a CRON job, ideally run every minute. 
The script will find all instances running in the same VPC filtered by the specified tag. 
The Ec2 instance must have an IAM instance profile assigned that gives it access to Ec2 API.

	update_haproxy.py --tag-name TAG_NAME --tag-value TAG_VALUE
	
	Update HAProxy to add all instances running in same VPC filtered by tag
	
	optional arguments:
	 --pid PID				The pid file for HAProxy. Defaults to /var/run/haproxy.pid
	 --template TEMPLATE	The template to use. Defaults to template/haproxy.template
	 --output OUTPUTFILE	The HAProxy configuration file to write to if changes detected. Defaults to /etc/haproxy/haproxy.cfg

Example:

	python update_haproxy.py --tag-name='type' --tag-value='orchestra'

Example cron job added to /etc/cron.d/update_haproxy: 	

	PATH=/usr/local/sbin:/usr/local/bin:/sbin:/bin:/usr/sbin:/usr/bin
	*/1 * * * * root cd /opt/haproxy-ec2-auto-discover && python update_haproxy.py --tag-name='type' --tag-value='orchestra' > /dev/null 2>&1
