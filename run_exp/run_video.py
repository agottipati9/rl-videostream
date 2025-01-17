import os
import sys
import signal
import subprocess
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException
from pyvirtualdisplay import Display
from time import sleep

from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

# TO RUN: download https://pypi.python.org/packages/source/s/selenium/selenium-2.39.0.tar.gz
# run sudo apt-get install python-setuptools
# run sudo apt-get install xvfb
# after untar, run sudo python setup.py install
# follow directions here: https://pypi.python.org/pypi/PyVirtualDisplay to install pyvirtualdisplay

# For chrome, need chrome driver: https://code.google.com/p/selenium/wiki/ChromeDriver
# chromedriver variable should be path to the chromedriver
# the default location for firefox is /usr/bin/firefox and chrome binary is /usr/bin/google-chrome
# if they are at those locations, don't need to specify


def timeout_handler(signum, frame):
	raise Exception("Timeout")

ip = sys.argv[1]
abr_algo = sys.argv[2]
run_time = int(sys.argv[3])
process_id = sys.argv[4]
trace_file = sys.argv[5]
sleep_time = sys.argv[6]
	
# prevent multiple process from being synchronized
sleep(int(sleep_time))
	
# generate url
url = 'http://' + ip + '/' + 'myindex_' + abr_algo + '.html'
# url = 'http://localhost:8333'  # DEBUG TEST QUERYING LOCALHOST

# timeout signal
signal.signal(signal.SIGALRM, timeout_handler)
signal.alarm(run_time + 30)
	
try:
	# copy over the chrome user dir
	default_chrome_user_dir = '/home/silver/Desktop/rl-videostream/abr_browser_dir/chrome_data_dir'
	chrome_user_dir = '/tmp/chrome_user_dir_id_' + process_id
	os.system('rm -r ' + chrome_user_dir)
	os.system('cp -r ' + default_chrome_user_dir + ' ' + chrome_user_dir)
	
	# start abr algorithm server
	if abr_algo == 'RL':
		command = 'exec /usr/bin/python /home/silver/Desktop/rl-videostream/rl_server/rl_server_no_training.py ' + trace_file
	elif abr_algo == 'fastMPC':
		command = 'exec /usr/bin/python /home/silver/Desktop/rl-videostream/rl_server/mpc_server.py ' + trace_file
	elif abr_algo == 'robustMPC':
		command = 'exec /usr/bin/python /home/silver/Desktop/rl-videostream/rl_server/robust_mpc_server.py ' + trace_file
	else:
		command = 'exec /usr/bin/python /home/silver/Desktop/rl-videostream/rl_server/simple_server.py ' + abr_algo + ' ' + trace_file
	
	proc = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
	sleep(2)
	
	# to not display the page in browser
	display = Display(visible=0, size=(800,600))
	display.start()

	print('initalizing chrome driver')
	
	# add logging
	d = DesiredCapabilities.CHROME
	d['goog:loggingPrefs'] = { 'browser':'ALL' }

	# initialize chrome driver
	options=Options()
	chrome_driver = '/home/silver/Desktop/rl-videostream/abr_browser_dir/chromedriver'
	options.add_argument('--user-data-dir=' + chrome_user_dir)
	options.add_argument('--disable-web-security')
	options.add_argument('--ignore-certificate-errors')
	options.add_argument('--autoplay-policy=no-user-gesture-required')
	driver=webdriver.Chrome(chrome_driver, chrome_options=options, desired_capabilities=d)

	print('initalized chrome driver')
	
	# run chrome
	driver.set_page_load_timeout(10)
	driver.get(url)

	print(f'fetched url: {url}')

	# After fetching the URL or at any point where you want to take the screenshot
	# driver.save_screenshot('./results/start.png')

	# print messages
	# for entry in driver.get_log('browser'):
	# 	print(entry)
	
	sleep(run_time)
	
	# After fetching the URL or at any point where you want to take the screenshot
	# driver.save_screenshot('./results/end.png')

	driver.quit()
	display.stop()
	
	# kill abr algorithm server
	proc.send_signal(signal.SIGINT)
	
	print('done')
	
except Exception as e:
	try: 
		display.stop()
	except:
		pass
	try:
		driver.quit()
	except:
		pass
	try:
		proc.send_signal(signal.SIGINT)
	except:
		pass
	
	print(e	)

