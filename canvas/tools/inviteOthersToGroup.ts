
import { tool } from "ai";
import { inviteOthersToGroupDataSchema } from "./aitm.schema.ts";
import { inviteOthersToGroup, InviteOthersToGroupData } from "..";

export default tool({
  description: `
  Invite others to a group
Sends an invitation to all supplied email addresses which will allow
the
receivers to join the group.
    `,
  parameters: inviteOthersToGroupDataSchema.omit({ url: true }),
  execute: async (args : Omit<InviteOthersToGroupData, "url"> ) => {
    try {
      const { data } = await inviteOthersToGroup(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    