
import { tool } from "ai";
import { rejectCourseInvitationDataSchema } from "./aitm.schema.ts";
import { rejectCourseInvitation, RejectCourseInvitationData } from "..";

export default tool({
  description: `
  Reject Course Invitation
rejects a pending course invitation for the current user
    `,
  parameters: rejectCourseInvitationDataSchema.omit({ url: true }),
  execute: async (args : Omit<RejectCourseInvitationData, "url"> ) => {
    try {
      const { data } = await rejectCourseInvitation(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    