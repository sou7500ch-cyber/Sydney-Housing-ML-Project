pipeline {
    agent any

    environment {
        PYTHON = 'python3'
        APP_PORT = '8501'
    }

    stages {

        stage('Build') {
            steps {
                echo '=== BUILD STAGE ==='
                sh '''
                    python3 --version
                    python3 -m venv .venv
                    .venv/bin/python -m pip install --upgrade pip
                    .venv/bin/pip install -r requirements.txt
                '''
            }
        }

        stage('Test') {
            steps {
                echo '=== TEST STAGE ==='
                sh '''
                    .venv/bin/pytest -v
                '''
            }
        }

        stage('Code Quality') {
            steps {
                echo '=== CODE QUALITY STAGE ==='
                sh '''
                    echo "Running Ruff static code analysis..."
                    .venv/bin/ruff check app.py database.py tests/
                    echo "Ruff quality gate PASSED."
                '''
            }
        }

        stage('Security') {
            steps {
                echo '=== SECURITY STAGE ==='
                sh '''
                    .venv/bin/pip install pip-audit
                    .venv/bin/pip-audit
                '''
            }
        }

        stage('Deploy') {
            steps {
                echo '=== DEPLOY STAGE ==='
                sh '''
                    mkdir -p deployment

                    cp app.py deployment/
                    cp database.py deployment/
                    cp model_features.pkl deployment/
                    cp sydney_housing_random_forest.pkl deployment/

                    echo "Application deployment package prepared."
                '''
            }
        }

        stage('Release') {
            steps {
                echo '=== RELEASE STAGE ==='
                sh '''
                    mkdir -p releases

                    tar -czf releases/sydney-housing-${BUILD_NUMBER}.tar.gz deployment/

                    echo "Release package created:"
                    ls -lh releases/
                '''
            }
        }

        stage('Monitoring') {
            steps {
                echo '=== MONITORING STAGE ==='
                sh '''
                    echo "Application health validation"

                    test -f deployment/app.py
                    test -f deployment/database.py
                    test -f deployment/sydney_housing_random_forest.pkl

                    echo "Health check PASSED."
                '''
            }
        }
    }

    post {

        success {
            echo '=== PIPELINE COMPLETED SUCCESSFULLY ==='
        }

        failure {
            echo '=== PIPELINE FAILED ==='
        }

        always {
            echo "Build number: ${BUILD_NUMBER}"
            echo "Pipeline result: ${currentBuild.currentResult}"
        }
    }
}