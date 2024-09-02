---Next.js Implementation WIP---

To run the application:
1. Clone the repository
2. Run npm i
3. put the .env file with DATABASE_URL set to the opencord database.
4. Run npm run dev

-if connecting to a new database and using provided prisma schema, will need to migrate with following:
  npx prisma generate
  npx prisma migrate dev --name init

'init' can be any name of your choosing, this will update schema of remote database to the provided schema.
