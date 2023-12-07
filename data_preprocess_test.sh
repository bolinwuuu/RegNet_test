
# soundlist=" "dog" "fireworks" "drum" "baby" "gun" "sneeze" "cough" "hammer" "
# soundlist=("dog" "fireworks" "drum" "baby" "gun" "sneeze" "cough" "hammer")
soundlist=("dog")
# soundlist=" "dogs" "cats" "birds" "

for soundtype in $soundlist 
do

    python extend_audio_10s_test.py \
    -i data/features/${soundtype}/audio_full \
    -o data/features/${soundtype}

    echo "data preprocess test done"

done