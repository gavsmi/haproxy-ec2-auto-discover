
import argparse
import logging
from ec2_auto_discover import get_instances
from mako.template import Template
import subprocess

def main():
    # parse cmd line args
    parser = argparse.ArgumentParser(description='Update haproxy to use all instances running in a VPC.')
    parser.add_argument('--tag-name', 
                            help='Name of tag to filter instances on')
    parser.add_argument('--tag-value', 
                            help='Value of tag to filter instances on')
    parser.add_argument('--pid', default='/var/run/haproxy.pid',
                            help='The pid file for haproxy. Defaults to /var/run/haproxy.pid.')
    parser.add_argument('--template', default='template/haproxy.template')
    parser.add_argument('--output', default='/etc/haproxy/haproxy.cfg',
                            help='Defaults to /etc/haproxy/haproxy.cfg if not specified.')
    
    args = parser.parse_args()
    
    # fetch all instances
    logging.info('Getting instances for vpc...')
    instances = get_instances(tag_name=args.tag_name, tag_value=args.tag_value)
    
    # generate new configuration
    logging.info('Generating new configuration...')
    new_config = Template(filename=args.template).render(instances=instances)
    
    # load existing configuration
    existing_config = get_file(fileName=args.output)

    # compare new against existing, if changed update and gracefully re-start haproxy
    logging.info('Comparing configurations...')
    if new_config != existing_config:
        logging.info('Existing configuration is outdated')
        
        # write new config
        write_file(fileName=args.output, content=new_config)
        
        # get haproxy pid
        pid = get_file(fileName=args.pid)
        
        # restart haproxy
        logging.info('Restarting HAProxy...')
        command = '''haproxy -p %s -f %s -sf %s''' % (args.pid, args.output, pid or '')
        logging.info('Executing: %s' % command)
        subprocess.call(command, shell=True)
    else:
        logging.info('Existing configuration is unchanged - skipping') 

def get_file(fileName=None):
    try:
        f = open(fileName, 'r')
        text = f.read()
        f.close()
    except:
        text = None
        
    return text

def write_file(fileName=None, content=None):
    f = open(fileName, 'w')
    f.write(content)
    f.close()

if __name__ == '__main__':
    logging.getLogger().setLevel(logging.INFO)
    main()
