
import { tool } from "ai";
import { listUserLoginsUsersDataSchema } from "./aitm.schema.ts";
import { listUserLoginsUsers, ListUserLoginsUsersData } from "..";

export default tool({
  description: `
  List user logins
Given a user ID, return a paginated list of that user's logins for the given
account.
    `,
  parameters: listUserLoginsUsersDataSchema.omit({ url: true }),
  execute: async (args : Omit<ListUserLoginsUsersData, "url"> ) => {
    try {
      const { data } = await listUserLoginsUsers(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    