import sys
import subprocess
import time
import os
import getopt
import ssl

def main(argv):
  try:
    st_scanner_jar = '/packages/nexus-iq-cli-1.38.0-02.jar'
    tl_scanner_exec = '/packages/twistcli'
    docker_image_id = os.environ.get('DOCKER_IMAGE_ID')
    st_application_id = os.environ.get('NEXUS_IQ_APPLICATION_ID')
    st_url = os.environ.get('NEXUS_IQ_URL')
    st_username = os.environ.get('NEXUS_IQ_USERNAME')
    st_password = os.environ.get('NEXUS_IQ_PASSWORD')
    st_stage = os.environ.get('NEXUS_IQ_STAGE')
    tl_console_hostname = os.environ.get('TL_CONSOLE_HOSTNAME')
    tl_console_port = os.environ.get('TL_CONSOLE_PORT')
    tl_console_username = os.environ.get('TL_CONSOLE_USERNAME')
    tl_console_password = os.environ.get('TL_CONSOLE_PASSWORD')
    tl_only = os.environ.get('TL_ONLY')
    java_home = os.environ.get('JAVA_HOME')
    java_keystore_password = os.environ.get('JAVA_KEYSTORE_PASSWORD')
    opts, args = getopt.getopt(argv,"h:i:a:j:u:p:s:t:E:T:P:U:X:Z:J:K:",["help","docker_image_id=","st_application_id=","st_scanner_jar=","st_url=","st_username=","st_password=","st_stage=","tl_scanner_exec=","tl_console_hostname","tl_console_port","tl_console_username=","tl_console_password=","tl_only","java_home=","java_keystore_password"])
  except getopt.GetoptError:
    print('Unrecognized Argument! See arguments list using -h or --help. Ex. twistlock.py --help')
    sys.exit(2)
  for opt, arg in opts:
    if opt == ("h","--help"):
      print('twistlock.py --arg value or twistlock.py -a value')
      print('-i --docker_image_id [DOCKER_IMAGE_ID] - Docker Image ID short or long IDs accepted')
      print('-a --st_application_id [NEXUS_IQ_APPLICATION_ID] - Applications ID in Nexus IQ')
      print('-j --st_scanner_jar - Location of nexus-iq-cli*.jar file')
      print('-u --st_username [NEXUS_IQ_USERNAME] - Nexus IQ Username')
      print('-p --st_password [NEXUS_IQ_PASSWORD] - Password for Nexus IQ Username')
      print('-s --st_url [NEXUS_IQ_URL] - Sonatype URL must be HTTPS with Valid Cert')
      print('-t --st_stage [NEXUS_IQ_STAGE] - Sonatype Stage')
      print('-E --tl_scanner_exec - Location of twistlock-scanner executable')
      print('-T --tl_console_hostname [TL_CONSOLE_HOSTNAME] - Twistlock Hostname with Valid Cert')
      print('-P --tl_console_port [TL_CONSOLE_PORT] - Twistock Console port')
      print('-U --tl_console_username [TL_CONSOLE_USERNAME] - Twistlock Console Username')
      print('-X --tl_console_password [TL_CONSOLE_PASSWORD] - Password for Twistlock Console Username')
      print('-Z --tl_only [TL_ONLY] - Set "TRUE" to run a stand-alone Twistlock Scan')
      print('-J --java_home [JAVA_HOME] - Java Home Directory (no trailing /)')
      print('-K --java_keystore_password [JAVA_KEYSTORE_PASSWORD] - Java Keystore Password')
      sys.exit()
    elif opt in ("-i", "--docker_image_id"):
      docker_image_id = arg
    elif opt in ("-a", "--st_application_id"):
      st_application_id = arg
    elif opt in ("-j", "--st_scanner_jar"):
      st_scanner_jar = arg
    elif opt in ("-s", "--st_url"):
      st_url = arg
    elif opt in ("-u", "--st_username"):
      st_username = arg
    elif opt in ("-p", "--st_password"):
      st_password = arg
    elif opt in ("-t", "--st_stage"):
      st_stage = arg
    elif opt in ("-E", "--tl_scanner_exec"):
      tl_scanner_exec = arg
    elif opt in ("-T", "--tl_console_hostname"):
      tl_console_hostname = arg
    elif opt in ('-P', "--tl_console_port"):
      tl_console_port = arg
    elif opt in ("-U", "--tl_console_username"):
      tl_console_username = arg
    elif opt in ('-X', "--tl_console_password"):
      tl_console_password = arg
    elif opt in ('-Z', "--tl_only"):
      tl_only = arg
    elif opt in ('-J', "--java_home"):
      java_home = arg
    elif opt in ('-K', "--java_keystore_password"):
      java_keystore_password = arg

  if tl_only == "TRUE": 
    # Run stand-alone Twistlock Scan
    command = ['/packages/twistcli -c https://' + tl_console_hostname + ':' + tl_console_port + ' -u ' + tl_console_username + ' -p ' + tl_console_password + ' -i ' + docker_image_id + ' --include-files --include-package-files --hash-method sha1']
    proc = subprocess.Popen(command, shell=True)
    stdout, stderr = proc.communicate()

  else:
    # Download and store site cert
    cert = ssl.get_server_certificate((tl_console_hostname, tl_console_port))
    print(cert,file=open("twistlock.cer", "w"))

    # Import site cert into java keystore
    command = ['keytool -importcert -noprompt -file twistlock.cer -alias twistlock -storepass ' + java_keystore_password + ' -keystore ' + java_home + '/jre/lib/security/cacerts']
    proc = subprocess.Popen(command, shell=True)
    stdout, stderr = proc.communicate()

    # Start Docker
    command = ['for i in {1..5}; do service docker start && break || sleep 15; done']
    proc = subprocess.Popen(command, shell=True)
    stdout, stderr = proc.communicate()
        
    # Run Twistlock Scan and send file to Sonatype
    command = ['java -cp ' + st_scanner_jar + ' com.sonatype.insight.scan.cli.TwistlockPolicyEvaluatorCli -i ' + st_application_id + ' -a "' + st_username + ':' + st_password + '" -s ' + st_url + ' --twistlock-scanner-executable ' + tl_scanner_exec + ' --twistlock-console-url https://' + tl_console_hostname + ':' + tl_console_port + ' --twistlock-console-username ' + tl_console_username + ' --twistlock-console-password "' + tl_console_password + '" --stage "' + st_stage + '" ' + docker_image_id]
    proc = subprocess.Popen(command, shell=True)
    stdout, stderr = proc.communicate()

if __name__ == "__main__":
  main(sys.argv[1:])