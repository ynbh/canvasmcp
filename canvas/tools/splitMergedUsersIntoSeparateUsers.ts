
import { tool } from "ai";
import { splitMergedUsersIntoSeparateUsersDataSchema } from "./aitm.schema.ts";
import { splitMergedUsersIntoSeparateUsers, SplitMergedUsersIntoSeparateUsersData } from "..";

export default tool({
  description: `
  Split merged users into separate users
Merged users cannot be fully restored to their previous
state, but this will
attempt to split as much as possible to the previous state.
To split a merged
user, the caller must have permissions to manage all of
the users logins. If there are multiple
users that have been merged into one
user it will split each merge into a separate user.
A split can
only happen within 180 days of a user merge. A user merge deletes
the previous user and may be
permanently deleted. In this scenario we create
a new user object and proceed to move as much as
possible to the new user.
The user object will not have preserved the name or settings from
the
previous user. Some items may have been deleted during a user_merge that
cannot be restored,
and/or the data has become stale because of other
changes to the objects since the time of the
user_merge.
    `,
  parameters: splitMergedUsersIntoSeparateUsersDataSchema.omit({ url: true }),
  execute: async (args : Omit<SplitMergedUsersIntoSeparateUsersData, "url"> ) => {
    try {
      const { data } = await splitMergedUsersIntoSeparateUsers(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    