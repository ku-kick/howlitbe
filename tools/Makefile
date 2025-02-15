# Prepares a Mininet VM for working w/ howlitbe
# RULES:
#
# $(OUT)/aptinstall-%:
# Will use apt to install the package defined by placeholder ($*).
# WARNING: if you want to make a special rule, e.g. "$(OUT)/aptinstall-custom-package", you MUST place it before
# $(OUT)/aptinstall-%:
#
# all:
# entrypoint rule

OUT=./out

post-mininet: $(OUT) $(OUT)/aptupdate $(OUT)/aptinstall-docker

$(OUT)/aptupdate:
	sudo apt update && touch $@

$(OUT):
	mkdir -p $@

$(OUT)/docker.deb: $(OUT)/aptinstall-curl $(OUT)/aptinstall-init-system-helpers
	@echo "Downloading docker"
	curl -L "https://github.com/ku-kick/kubin/releases/download/0.0.1/docker.deb" -o $@

$(OUT)/download-%:
	curl -L $* -o $(OUT)/$*
	touch $@

$(OUT)/aptinstall-docker: $(OUT)/aptinstall-docker-compose-plugin_2.6.0~ubuntu-bionic_arm64.deb $(OUT)/aptinstall-docker-ce_24.0.2-1~ubuntu.18.04~bionic_arm64.deb

# Install docker, create a marker file telling us that docker is aptinstall
#$(OUT)/aptinstall-docker: $(OUT)/docker.deb
#	@echo Installing docker from $<
#	if ! sudo dpkg -i $< ; then sudo apt install --fix-broken ; fi
#	sudo dpkg -i $< && touch $@

$(OUT)/aptinstall-%:
	@echo "Trying to install $* using apt..."
	sudo apt install $* --reinstall && touch $@

clean:
	rm -rf $(OUT)
