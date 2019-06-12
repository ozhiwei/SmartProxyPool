#!/bin/sh

echo "Start Pull Image          ========"
echo
ssh -o StrictHostKeyChecking=no root@$DEPLOY_SSH_HOST -p$DEPLOY_SSH_PORT "docker pull 1again/proxy_pool"
echo

echo "Start Update Code    ========"
echo
ssh -o StrictHostKeyChecking=no root@$DEPLOY_SSH_HOST -p$DEPLOY_SSH_PORT "cd $WORKDIR && git pull"
echo

echo "Start Update Container    ========"
echo
ssh -o StrictHostKeyChecking=no root@$DEPLOY_SSH_HOST -p$DEPLOY_SSH_PORT "cd $WORKDIR && docker-compose -f Docker/docker-compose.yml up -d"
echo