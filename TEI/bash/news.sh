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
NOTA=('ras1' 'ras2' 'ras1_og_2' 'stod2' 'bylgjan' 'sjonvarpid' '433' 'vf_kylfingur' 'bleikt')
CONFIGFILE='/home/starkadur/PycharmProjects/TEI/frettir/config/main_ana_news.json'
FOLDER='/media/starkadur/NewVolume/risamalheild2020/frettir/'${LICENCE}'/IGC-News'${nr}'-21.05.TEI/'

for path in ${FOLDER}*;do
  midill="${path##*/}"


  if [[ " ${NOTA[@]} " =~ " ${midill} " ]]; then

    id=${midill/_/}

    echo "###### "${midill}" ####"
    input="/media/starkadur/NewVolume/risamalheild2020/frettir/"${LICENCE}"/IGC-News"${nr}"-21.05.TEI/"${midill}"/"
    output="/media/starkadur/NewVolume/risamalheild2020/frettir/"${LICENCE}"/IGC-News"${nr}"-21.05.ana/"${midill}"/"
    teicorpus="/media/starkadur/NewVolume/risamalheild2020/frettir/"${LICENCE}"/IGC-News"${nr}"-21.05.TEI/"${midill}"/IGC-News"${nr}"-"${id}"-21.05.xml"

    python3 ../tok_tag_lem.py --input ${input} --output ${output} --configfile ${CONFIGFILE} --teiCorpus ${teicorpus} --reverse 1
  fi;
done;
