
import { tool } from "ai";
import { mergeUserIntoAnotherUserDestinationUserIdDataSchema } from "./aitm.schema.ts";
import { mergeUserIntoAnotherUserDestinationUserId, MergeUserIntoAnotherUserDestinationUserIdData } from "..";

export default tool({
  description: `
  Merge user into another user
Merge a user into another user.
To merge users, the caller must have
permissions to manage both users. This
should be considered irreversible. This will delete the user
and move all
the data into the destination user.

When finding users by SIS ids in different
accounts the
destination_account_id is required.

The account can also be identified by passing the
domain in destination_account_id.
    `,
  parameters: mergeUserIntoAnotherUserDestinationUserIdDataSchema.omit({ url: true }),
  execute: async (args : Omit<MergeUserIntoAnotherUserDestinationUserIdData, "url"> ) => {
    try {
      const { data } = await mergeUserIntoAnotherUserDestinationUserId(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    