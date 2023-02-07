HOSTNAME := `hostname -f`

prod:
	HOSTNAME=${HOSTNAME} docker-compose up

dev:
	HOSTNAME=${HOSTNAME} docker-compose -f docker-compose.yaml -f docker-compose-test.yaml up

