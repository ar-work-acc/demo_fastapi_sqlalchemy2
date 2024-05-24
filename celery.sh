#!/bin/bash

current_directory=$(pwd)
CELERY_LOG_FILE="${current_directory}/celery.log"
CELERY_PID_FILE="${current_directory}/celery.pid"
CELERY_APP="task_queue.tasks"  # Replace with your Celery application name

start_celery() {
    echo "Starting Celery worker..."
    nohup celery -A $CELERY_APP worker -Q default --loglevel=DEBUG > $CELERY_LOG_FILE 2>&1 &
    CELERY_PID=$!
    echo $CELERY_PID > $CELERY_PID_FILE
    echo "Celery worker started with PID $CELERY_PID."
}

stop_celery() {
    if [ -f $CELERY_PID_FILE ]; then
        CELERY_PID=$(cat $CELERY_PID_FILE)
        echo "Stopping Celery worker with PID $CELERY_PID..."
        kill $CELERY_PID
        rm $CELERY_PID_FILE
        echo "Celery worker stopped."
    else
        echo "No PID file found. Is the Celery worker running?"
    fi
}

# Check the first argument passed to the script
case "$1" in
  start)
    cd src || exit
    echo "Redis CLI: FLUSHALL!"
    redis-cli --user admin --pass pw2024 FLUSHALL
    start_celery
    cd ..
    ;;
  stop)
    stop_celery
    ;;
  *)
    echo "Usage: $0 {start|stop}"
    exit 1
    ;;
esac
