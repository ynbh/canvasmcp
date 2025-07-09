
import { tool } from "ai";
import { listUserParticipantsDataSchema } from "./aitm.schema.ts";
import { listUserParticipants, ListUserParticipantsData } from "..";

export default tool({
  description: `
  List user participants
A paginated list of users that are (or may be) participating in
this
appointment group.  Refer to the Users API for the response fields. Returns
no results for
appointment groups with the "Group" participant_type.
    `,
  parameters: listUserParticipantsDataSchema.omit({ url: true }),
  execute: async (args : Omit<ListUserParticipantsData, "url"> ) => {
    try {
      const { data } = await listUserParticipants(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    