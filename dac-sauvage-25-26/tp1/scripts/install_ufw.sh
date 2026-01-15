for i in {1..4}
do 
    ssh comp$i "sudo apt update && sudo apt install ufw"
done    