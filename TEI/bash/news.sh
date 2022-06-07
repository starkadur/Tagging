#!/bin/bash
LICENCE=$1

if [[ "$LICENCE" == "CC_BY" ]];
then
  nr=1
elif [[ "$LICENCE" == "MIM" ]];
then
  nr=2
else
  echo "NR er rangt"
  echo $LICENCE
  exit
fi
#NOTA=('ras1' 'ras2' 'ras1_og_2' 'stod2' 'bylgjan' 'sjonvarpid' '433' 'vf_kylfingur' 'bleikt')
CONFIGFILE='/home/starkadur/config/main_ana_news.json'
FOLDER='/mnt/gagnageymsla/starkadur/IGC-22/frettir/'${LICENCE}'/IGC-News'${nr}'-22.10.TEI/'

for path in ${FOLDER}*;do
  midill="${path##*/}"


  #if [[ " ${NOTA[@]} " =~ " ${midill} " ]]; then

    id=${midill/_/}

    echo "###### "${midill}" ####"
    input="/mnt/gagnageymsla/starkadur/IGC-22/frettir/"${LICENCE}"/IGC-News"${nr}"-22.10.TEI/"${midill}"/"
    output="/mnt/gagnageymsla/starkadur/IGC-22/frettir/"${LICENCE}"/IGC-News"${nr}"-22.10.ana/"${midill}"/"
    teicorpus="/mnt/gagnageymsla/starkadur/IGC-22/frettir/"${LICENCE}"/IGC-News"${nr}"-22.10.TEI/"${midill}"/IGC-News"${nr}"-"${id}"-22.10.xml"

    python3 tok_tag_lem.py --input ${input} --output ${output} --configfile ${CONFIGFILE} --teiCorpus ${teicorpus} --reverse 1
  #fi;
done;
