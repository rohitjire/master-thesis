# latexmk configuration for this thesis.
#
# WHY THIS FILE EXISTS: the glossaries package writes the acronym list to main.acn,
# and a separate program (makeglossaries) has to turn that into main.acr before the
# "List of Abbreviations" page has anything to print. latexmk does not know about that
# step on its own, and main.acr is a build artefact excluded by .gitignore -- so on a
# fresh clone the page silently renders empty. These rules teach latexmk to run
# makeglossaries itself, which makes the build reproduce on any machine.

add_cus_dep('acn', 'acr', 0, 'run_makeglossaries');   # acronyms  -> List of Abbreviations
add_cus_dep('glo', 'gls', 0, 'run_makeglossaries');   # glossary  -> Glossary (unused here)

sub run_makeglossaries {
    my ($base_name, $path) = fileparse($_[0]);
    pushd $path;
    my $return = system('makeglossaries', $base_name);
    popd;
    return $return;
}

# let "latexmk -c" clean the glossary artefacts too
push @generated_exts, 'acn', 'acr', 'alg', 'glo', 'gls', 'glg';
