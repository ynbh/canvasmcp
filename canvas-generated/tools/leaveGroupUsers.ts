
import { tool } from "ai";
import { leaveGroupUsersDataSchema } from "./aitm.schema.ts";
import { leaveGroupUsers, LeaveGroupUsersData } from "..";

export default tool({
  description: `
  Leave a group
Leave a group if you are allowed to leave (some groups, such as sets of
course groups
created by teachers, cannot be left). You may also use 'self'
in place of a membership_id.
    `,
  parameters: leaveGroupUsersDataSchema.omit({ url: true }),
  execute: async (args : Omit<LeaveGroupUsersData, "url"> ) => {
    try {
      const { data } = await leaveGroupUsers(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    