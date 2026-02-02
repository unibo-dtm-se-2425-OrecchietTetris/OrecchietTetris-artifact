module.exports = {
    extends: ['@commitlint/config-conventional'],
    rules: {
        'type-enum': [
            2,
            'always',
            [
                'feat',     // nuova feature
                'fix',      // bug fix
                'docs',     // solo documentazione
                'style',    // formattazione, no code change
                'refactor', // refactoring
                'perf',     // performance
                'test',     // aggiunta test
                'chore',    // build, config, etc
                'revert',   // revert commit
                'ci',       // CI/CD
            ],
        ],
        'subject-case': [2, 'never', ['sentence-case', 'start-case', 'pascal-case']],
        'header-max-length': [2, 'always', 1000]
    }
};
