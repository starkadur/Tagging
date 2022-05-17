

CONFIGFILE='/home/starkadur/PycharmProjects/TEI/samfelagsmidlar/config/main_ana_samfelagsmidlar.json'
FOLDER='/media/starkadur/NewVolume/risamalheild2020/samfelagsmidlar/TEI/IGC-Social-21.10.TEI/Blog/'

for path in ${FOLDER}*;do
    midill="${path##*/}"
    if [[ "$midill" == *xml ]]
    then
      continue
    fi
    if [[ "$midill" == *ndriki ]]
    then
      continue
    fi

    id=${midill/_/}

    echo "###### "${midill}" ####"
    input="/media/starkadur/NewVolume/risamalheild2020/samfelagsmidlar/TEI/IGC-Social-21.10.TEI/Blog/"${midill}"/"
    output="/media/starkadur/NewVolume/risamalheild2020/samfelagsmidlar/TEI/IGC-Social-21.10.ana/Blog/"${midill}"/"
    teicorpus="/media/starkadur/NewVolume/risamalheild2020/samfelagsmidlar/TEI/IGC-Social-21.10.TEI/Blog/"${midill}"/IGC-Social2-"${id}"-21.10.xml"

    python3 ../tok_tag_lem.py --input ${input} --output ${output} --configfile ${CONFIGFILE} --teiCorpus ${teicorpus} --reverse 1

done;
