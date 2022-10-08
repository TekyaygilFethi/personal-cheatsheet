# personal-cheetsheet

Description will be added

## Set-up

To use the application you must use Redis. Here, Docker is being suggested for managing Redis instances. Download and install Docker on your service. Then execute this command to run Redis on Docker:
```bash
  $ docker run --name my-redis -p 6379:6379 -d redis
```

## To-Do's

- [x] Dockerfile
- [x] Migrate DB to deta.sh bases [please check deta branch]
- [x] Add Redis cache suuport
- [ ] Add more neatsheet
- [ ] Write readme.md
- [ ] Add neatsheet tag feature
- [ ] Make all neatsheets seperatable by block
