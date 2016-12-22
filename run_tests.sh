# Run all tests included in each of the corresponding files.
#
# Juan Pablo de la Cruz Gutierrez

print_help()
{
cat <<HELP
$0 [-w]
  -c in addition to unit tests, run code coverage
  -w generate HTML report of code coverage
  -h print this help message
HELP
}

codecov=false
output="report"
while getopts "whc" opt; do
  case $opt in
    "h")
      print_help && exit 0
      ;;
    "w")
      output="html"
      ;;
    "c")
      codecov=true
      ;;
    *)
      echo "Unexpected option: $opt" >&2
      ;;
  esac
done
shift $((OPTIND-1))


# modules=$(ls pyroff/*py | tr '/' '.' | sed 's,\.py$,,' | xargs)
modules="pyeqn pytbl eqn2latex tbl2html ast eqn"

for mod in $modules
do
  echo Run tests in "pyroff.$mod"
  python3 -m "pyroff.$mod"
done

[[ $codecov == "false" ]] && exit 0

coverage=$(which coverage3)
coverage=$(which coverage)
[[ -z $coverage ]] && coverage=$(which python3-coverage)
[[ -z $coverage ]] && coverage=$(which python2-coverage)

if [[ $coverage ]]
then
  for mod in $modules
  do
    $coverage run -a -m "pyroff.$mod"
  done
  $coverage $output
else
  echo "Install the coverage module if you wish to get a " \
"report on code coverage" >&2
fi
