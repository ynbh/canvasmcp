
import { tool } from "ai";
import { createAppointmentGroupDataSchema } from "./aitm.schema.ts";
import { createAppointmentGroup, CreateAppointmentGroupData } from "..";

export default tool({
  description: `
  Create an appointment group
Create and return a new appointment group. If new_appointments
are
specified, the response will return a new_appointments array (same format
as appointments array,
see "List appointment groups" action)
    `,
  parameters: createAppointmentGroupDataSchema.omit({ url: true }),
  execute: async (args : Omit<CreateAppointmentGroupData, "url"> ) => {
    try {
      const { data } = await createAppointmentGroup(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    