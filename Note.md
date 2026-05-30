docker-compose -f docker-compose_default.yaml config

JAVA_OPTS: "-javaagent:/kieker/kieker-2.0.3-aspectj.jar"
    volumes:
      - ./kieker:/kieker
      - ./logs/auth:/tmp/kieker
cd ~/KLTN/TeaStore/examples/docker
cd ~/KLTN/TeaStore/services/tools.descartes.teastore.recommender/src/main/java/tools/descartes/teastore/recommender/rest

sudo docker-compose -f docker-compose_default.yaml down
sudo docker-compose -f docker-compose_default.yaml up -d

docker network create teastore-network
docker compose -f docker-compose_kieker.yaml config

docker compose -f docker-compose_kieker.yaml up --build

jmeter -n -t teastore.jmx -l results_baseline.jtl \
-Jxstream.allowlist=org.apache.jmeter.save.ScriptWrapper

cd ~/apache-jmeter-5.4.1/bin
./jmeter -n \
-t ~/KLTN/teastore.jmx \
-Jhost=localhost \
-Jport=8080 \
-Jthread=50 \
-Jrps=20 \
-Jduration=60 \
-Jwarmup=10 \
-l result.jtl

sudo rm -rf ~/KLTN/TeaStore/examples/docker/logs/webui/*


docker logs docker-webui-1 | grep kieker
docker logs docker-webui-1


cd ~/KLTN/TeaStore
mvn clean install -DskipTests


// kiểm tra
top


cd ~/KLTN/TeaStore/examples/docker
cp docker-compose_default.yaml docker-compose_injected.yaml


nano docker-compose_injected.yaml
#image: teastore-recommender:injected


cd ~/KLTN/TeaStore/services/tools.descartes.teastore.recommender/
mvn clean package
sudo docker build -t descartesresearch/teastore-recommender:injected .

cd ~/KLTN/TeaStore/examples/docker

sudo docker-compose -f docker-compose_default.yaml down
sudo docker-compose -f docker-compose_injected.yaml up -d
sleep 15

q()


huong@DESKTOP-N8HQT6B:~/KLTN/TeaStore/examples/docker$ docker network create teastore-network
b6b7ed80afa823a11ea0f361645c62178947ec5ce14bb20724d7963f31e00a8f