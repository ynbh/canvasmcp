
import { tool } from "ai";
import { updateAppointmentGroupDataSchema } from "./aitm.schema.ts";
import { updateAppointmentGroup, UpdateAppointmentGroupData } from "..";

export default tool({
  description: `
  Update an appointment group
Update and return an appointment group. If new_appointments are
specified,
the response will return a new_appointments array (same format as
appointments array, see
"List appointment groups" action).
    `,
  parameters: updateAppointmentGroupDataSchema.omit({ url: true }),
  execute: async (args : Omit<UpdateAppointmentGroupData, "url"> ) => {
    try {
      const { data } = await updateAppointmentGroup(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    