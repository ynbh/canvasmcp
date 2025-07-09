
import { tool } from "ai";
import { acceptCourseInvitationDataSchema } from "./aitm.schema.ts";
import { acceptCourseInvitation, AcceptCourseInvitationData } from "..";

export default tool({
  description: `
  Accept Course Invitation
accepts a pending course invitation for the current user
    `,
  parameters: acceptCourseInvitationDataSchema.omit({ url: true }),
  execute: async (args : Omit<AcceptCourseInvitationData, "url"> ) => {
    try {
      const { data } = await acceptCourseInvitation(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    