pipeline {
    agent any

    environment {
        PYTHON = 'python3'
        APP_PORT = '8502'
        APP_NAME = 'sydney-housing'
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

                    echo "Application files copied to staging deployment."

                    echo "Starting Streamlit staging deployment..."

                    nohup .venv/bin/python -m streamlit run deployment/app.py \
                        --server.headless true \
                        --server.port ${APP_PORT} \
                        > deployment/streamlit.log 2>&1 &

                    echo $! > deployment/streamlit.pid

                    echo "Streamlit staging process started."
                    echo "Process ID:"
                    cat deployment/streamlit.pid

                    echo "Staging port: ${APP_PORT}"
                '''
            }
        }

        stage('Release') {
            steps {
                echo '=== RELEASE STAGE ==='
                sh '''
                    mkdir -p releases

                    VERSION="v1.0.${BUILD_NUMBER}"
                    RELEASE_FILE="${APP_NAME}-${VERSION}.tar.gz"
                    RELEASE_DATE=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
                    GIT_COMMIT=$(git rev-parse --short HEAD)

                    echo "Release version: ${VERSION}"
                    echo "Git commit: ${GIT_COMMIT}"
                    echo "Release date: ${RELEASE_DATE}"

                    cat > deployment/release-info.txt <<EOF
Application: ${APP_NAME}
Version: ${VERSION}
Jenkins Build: ${BUILD_NUMBER}
Git Commit: ${GIT_COMMIT}
Release Date: ${RELEASE_DATE}
Environment: staging
EOF

                    tar -czf "releases/${RELEASE_FILE}" deployment/

                    echo "Release package created:"
                    ls -lh "releases/${RELEASE_FILE}"

                    echo "Release metadata:"
                    cat deployment/release-info.txt

                    echo "Creating Git release tag..."

                    if git rev-parse "${VERSION}" >/dev/null 2>&1
                    then
                        echo "Git tag ${VERSION} already exists locally."
                    else
                        git tag -a "${VERSION}" -m "Release ${VERSION}"
                    fi

                    echo "Pushing Git release tag to GitHub..."

                    git push origin "${VERSION}"

                    echo "Git release tag pushed successfully:"
                    git ls-remote --tags origin "refs/tags/${VERSION}"
                '''
            }
        }

        stage('Monitoring') {
            steps {
                echo '=== MONITORING STAGE ==='
                sh '''
                    echo "Checking Streamlit staging application..."

                    for i in 1 2 3 4 5 6 7 8 9 10
                    do
                        if curl -fsS http://localhost:${APP_PORT} > /dev/null
                        then
                            echo "Health check PASSED."
                            echo "Streamlit staging application is responding on port ${APP_PORT}."
                            exit 0
                        fi

                        echo "Waiting for application to start... attempt $i/10"
                        sleep 2
                    done

                    echo "Health check FAILED."
                    echo "Streamlit application did not respond on port ${APP_PORT}."

                    if [ -f deployment/streamlit.log ]
                    then
                        echo "=== STREAMLIT LOG ==="
                        cat deployment/streamlit.log
                    fi

                    exit 1
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
            echo '=== CLEANUP STAGE ==='
            sh '''
                if [ -f deployment/streamlit.pid ]
                then
                    PID=$(cat deployment/streamlit.pid)

                    if kill -0 "$PID" 2>/dev/null
                    then
                        echo "Stopping Streamlit staging process: $PID"
                        kill "$PID" || true
                    else
                        echo "Streamlit process $PID is no longer running."
                    fi
                else
                    echo "No Streamlit process file found."
                fi
            '''

            echo "Build number: ${BUILD_NUMBER}"
            echo "Pipeline result: ${currentBuild.currentResult}"
        }
    }
}
