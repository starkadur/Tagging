

CONFIGFILE='/home/staba/Tagging/config/main_ana_parla.json'
FOLDER='/mnt/gagnageymsla/starkadur/IGC-22/social/IGC-Social-22.10.TEI/Blog/'

for path in ${FOLDER}*;do
    midill="${path##*/}"
    if [[ "$midill" == *xml ]]
    then
      continue
    fi

    id=${midill/_/}

    echo "###### "${midill}" ####"
    
    input="/mnt/gagnageymsla/starkadur/IGC-22/social/IGC-Social-22.10.TEI/Blog/"${midill}"/"
    output="/mnt/gagnageymsla/starkadur/IGC-22/social/IGC-Social-22.10.ana/BLog/"${midill}"/"
    teicorpus="/mnt/gagnageymsla/starkadur/IGC-22/social/IGC-Social-22.10.TEI/Blog/"${midill}"/IGC-Social2-"${id}"-22.10.xml"

    python3 tok_tag_lem.py --input ${input} --output ${output} --configfile ${CONFIGFILE} --teiCorpus ${teicorpus} --reverse 1

done;
