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
                    mkdir -p monitoring

                    echo "Starting application monitoring..."

                    if [ ! -f deployment/streamlit.pid ]
                    then
                        echo "CRITICAL ALERT: Streamlit PID file is missing."
                        exit 1
                    fi

                    PID=$(cat deployment/streamlit.pid)

                    echo "Monitored process: $PID"
                    echo "Monitoring port: ${APP_PORT}"

                    if ! kill -0 "$PID" 2>/dev/null
                    then
                        echo "CRITICAL ALERT: Streamlit process is not running."
                        exit 1
                    fi

                    HTTP_RESULT=$(curl -fsS \
                        -o /dev/null \
                        -w "%{http_code} %{time_total}" \
                        http://localhost:${APP_PORT})

                    HTTP_STATUS=$(echo "$HTTP_RESULT" | awk '{print $1}')
                    RESPONSE_TIME=$(echo "$HTTP_RESULT" | awk '{print $2}')

                    CPU_USAGE=$(ps -p "$PID" -o %cpu= | tr -d ' ')
                    MEMORY_KB=$(ps -p "$PID" -o rss= | tr -d ' ')

                    if [ -z "$CPU_USAGE" ]
                    then
                        CPU_USAGE="0"
                    fi

                    if [ -z "$MEMORY_KB" ]
                    then
                        MEMORY_KB="0"
                    fi

                    MEMORY_MB=$(python3 -c "print(f'{int(${MEMORY_KB}) / 1024:.2f}')")

                    echo "=== LIVE MONITORING METRICS ==="
                    echo "HTTP status: ${HTTP_STATUS}"
                    echo "Response time: ${RESPONSE_TIME} seconds"
                    echo "CPU usage: ${CPU_USAGE}%"
                    echo "Memory usage: ${MEMORY_MB} MB"
                    echo "Process ID: ${PID}"

                    cat > monitoring/metrics.txt <<EOF
Application: ${APP_NAME}
Jenkins Build: ${BUILD_NUMBER}
Monitoring Time: $(date -u +"%Y-%m-%dT%H:%M:%SZ")
HTTP Status: ${HTTP_STATUS}
Response Time: ${RESPONSE_TIME} seconds
CPU Usage: ${CPU_USAGE}%
Memory Usage: ${MEMORY_MB} MB
Process ID: ${PID}
Port: ${APP_PORT}
EOF

                    echo "=== ALERT RULES ==="

                    ALERT_TRIGGERED=false

                    if [ "${HTTP_STATUS}" != "200" ]
                    then
                        echo "ALERT: HTTP health check failed."
                        ALERT_TRIGGERED=true
                    fi

                    RESPONSE_LIMIT="2.0"

                    if awk "BEGIN {exit !(${RESPONSE_TIME} > ${RESPONSE_LIMIT})}"
                    then
                        echo "ALERT: Response time exceeded ${RESPONSE_LIMIT} seconds."
                        ALERT_TRIGGERED=true
                    fi

                    if [ "${ALERT_TRIGGERED}" = "true" ]
                    then
                        echo "MONITORING ALERT: One or more thresholds were exceeded."
                        echo "Alert state: TRIGGERED" > monitoring/alert.log
                    else
                        echo "All monitoring thresholds are healthy."
                        echo "Alert state: CLEAR" > monitoring/alert.log
                    fi

                    echo "=== INCIDENT SIMULATION ==="
                    echo "Simulating an unavailable service on port 8599..."

                    if curl -fsS --max-time 2 http://localhost:8599 > /dev/null 2>&1
                    then
                        echo "INCIDENT SIMULATION FAILED: Unexpected service response."
                        exit 1
                    else
                        echo "ALERT SIMULATION: Unavailable service detected."
                        echo "Incident alert successfully triggered."
                    fi

                    echo "=== RECOVERY VERIFICATION ==="

                    RECOVERY_STATUS=$(curl -fsS \
                        -o /dev/null \
                        -w "%{http_code}" \
                        http://localhost:${APP_PORT})

                    if [ "${RECOVERY_STATUS}" = "200" ]
                    then
                        echo "Recovery verification PASSED."
                        echo "Application returned HTTP ${RECOVERY_STATUS} after incident simulation."
                    else
                        echo "Recovery verification FAILED."
                        exit 1
                    fi

                    echo "=== MONITORING SUMMARY ==="
                    cat monitoring/metrics.txt
                    cat monitoring/alert.log

                    echo "Monitoring and alerting checks PASSED."
                '''
            }
        }
    }

    post {

        success {
            echo '=== PIPELINE COMPLETED SUCCESSFULLY ==='

            archiveArtifacts artifacts: 'monitoring/metrics.txt, monitoring/alert.log, deployment/streamlit.log, releases/*.tar.gz',
                             allowEmptyArchive: false,
                             fingerprint: true

            echo 'Monitoring reports and release artifacts archived successfully.'
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
