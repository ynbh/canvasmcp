
import { tool } from "ai";
import { listStudentGroupParticipantsDataSchema } from "./aitm.schema.ts";
import { listStudentGroupParticipants, ListStudentGroupParticipantsData } from "..";

export default tool({
  description: `
  List student group participants
A paginated list of student groups that are (or may be)
participating in
this appointment group. Refer to the Groups API for the response fields.
Returns no
results for appointment groups with the "User" participant_type.
    `,
  parameters: listStudentGroupParticipantsDataSchema.omit({ url: true }),
  execute: async (args : Omit<ListStudentGroupParticipantsData, "url"> ) => {
    try {
      const { data } = await listStudentGroupParticipants(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    