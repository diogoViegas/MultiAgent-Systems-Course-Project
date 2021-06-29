all:
	echo "#!/bin/sh\npython3.8 src/Main.py\n" > Main
	chmod 755 Main

clean:
	rm -f Main
