# Run all tests included in each of the corresponding files.
#
# Juan Pablo de la Cruz Gutierrez

coverage=$(which coverage3)
coverage=$(which coverage)
[[ -z $coverage ]] && coverage=$(which python3-coverage)
[[ -z $coverage ]] && coverage=$(which python2-coverage)

# modules=$(ls pyroff/*py | tr '/' '.' | sed 's,\.py$,,' | xargs)
modules="pyeqn pytbl eqn2latex tbl2html ast"

for mod in $modules
do
  echo python3 -m "pyroff.$mod"
  python3 -m "pyroff.$mod"
done

if [[ $coverage ]]
then
  for mod in $modules
  do
    $coverage run -a -m "pyroff.$mod"
  done
  $coverage report
else
  echo "Install the coverage module if you wish to get a " \
"report on code coverage" >&2
fi
