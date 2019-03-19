clear
printf "" > errors # Clear out errors from possible previous runs

while read line; do
    pip install $line

    if [ $? -ne 0 ]; then
        printf "ERROR INSTALLING: $line\n" >> errors
    fi

    printf "##################################################################\n"
done < "./requirements.txt"