
import { tool } from "ai";
import { getEffectiveDueDatesDataSchema } from "./aitm.schema.ts";
import { getEffectiveDueDates, GetEffectiveDueDatesData } from "..";

export default tool({
  description: `
  Get effective due dates
For each assignment in the course, returns each assigned student's ID
and
their corresponding due date along with some grading period data.
Returns a collection with keys
representing assignment IDs and values as a
collection containing keys representing student IDs and
values representing
the student's effective due_at, the grading_period_id of which the due_at
falls
in, and whether or not the grading period is closed (in_closed_grading_period)

The list of
assignment IDs for which effective student due dates are
requested. If not provided, all assignments
in the course will be used.
    `,
  parameters: getEffectiveDueDatesDataSchema.omit({ url: true }),
  execute: async (args : Omit<GetEffectiveDueDatesData, "url"> ) => {
    try {
      const { data } = await getEffectiveDueDates(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    