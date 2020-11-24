#!/bin/bash

# start.sh:
# Starts the main program using given settings
#

# Clean Last Usage
# Removing Client Logs
rm client_log_?.log
# Removing Hostfile
rm hostfile

RED="\033[1;31m"
GREEN="\033[1;32m"
NOCOLOR="\033[0m"
BOLD="\033[1m"

echo -e "#$BOLD$GREEN Pyraft $NOCOLOR\n"
echo -e "## Authors\n\n* Victor Guichard\n* Guillaume Valente\n"

# Asking for settings
echo -e "### Settings:\n"

echo -ne "Number of$BOLD$RED Clients$NOCOLOR (default 2): "
read clientNumber

echo -n "Client mean log size (default 5): "
read logSize

echo -ne "Number of$BOLD$RED Servers$NOCOLOR (default 3): "
read serverNumber

# Generating client logs
echo -ne "\n--> Generating client logs... "

if [ -z "$clientNumber" ]; then
    clientNumber="2"
fi

if [ -z "$serverNumber" ]; then
    serverNumber="3"
fi

if [ -z "$logSize" ]; then
    python3 client_datagen.py --nb_client $clientNumber
else
    python3 client_datagen.py --nb_client $clientNumber --mean_log_size $logSize
fi

echo "Done. <--"

# Generating MPI hostfile
totalProcess=$(( clientNumber + serverNumber + 1 )) # +1 For REPL

echo -n "--> Generating Hostfile... "
echo -n "localhost slots=$totalProcess" > hostfile
echo "Done. <--"

echo "--> Starting Raft <--"
echo "To stop the program: CTRL+C or STOP then EXIT"

# Start MPI processes

echo "mpirun -n $totalProcess -hostfile hostfile python3 main.py $clientNumber"
mpirun -n $totalProcess -hostfile hostfile python3 main.py $clientNumber