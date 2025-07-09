
import { tool } from "ai";
import { listUsersInAccountDataSchema } from "./aitm.schema.ts";
import { listUsersInAccount, ListUsersInAccountData } from "..";

export default tool({
  description: `
  List users in account
A paginated list of of users associated with this account.
    `,
  parameters: listUsersInAccountDataSchema.omit({ url: true }),
  execute: async (args : Omit<ListUsersInAccountData, "url"> ) => {
    try {
      const { data } = await listUsersInAccount(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    