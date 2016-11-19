build:
	sudo apt-get install python-kazoo sshpass
	docker build -t pviotti/zk:v1 .

run:
	python zk_part.py

clean:
	rm -f zoo.cfg
