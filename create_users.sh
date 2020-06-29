#!/bin/sh
#Purpose: Automate New User Creation

#Prompt for new username
read -p 'Enter New Username: ' user_name

#Create user
useradd $user_name

#Create user home directory
mkdir -p /home/$user_name

#Create SSH directory and authorized key file
mkdir -p /home/$user_name/.ssh
touch /home/$user_name/.ssh/authorized_keys

#Change directory to specific user
cd /home/$user_name/.ssh

#Create SSH key pair
yes "y" | ssh-keygen -f $user_name -t rsa -N "" -f id_rsa

#Copy key to authorized keys
cat id_rsa.pub >> authorized_keys

#Set permissions
chown -R $user_name:$user_name /home/$user_name/
chmod 700 /home/$user_name/.ssh
chmod 600 /home/$user_name/.ssh/authorized_keys

#Script complete read out new username
echo
echo
echo $user_name was created.
echo
echo
echo Please copy this SSH key file for $user_name
echo
echo
cat /home/$user_name/.ssh/id_rsa
