tmux attach || tmux
sudo apt update && sudo apt upgrade -y
sudo apt install python3 python3-dev python3.10-venv -y

git clone https://github.com/anti177/HappyCodingEnd.git
cd HappyCodingEnd || exit
python3 -m venv venv && source venv/bin/activate
pip install imageio imageio-ffmpeg moviepy flask flask_cors boto3
mkdir credentials # Put credentials there
python app.py
