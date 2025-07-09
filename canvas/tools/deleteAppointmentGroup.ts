
import { tool } from "ai";
import { deleteAppointmentGroupDataSchema } from "./aitm.schema.ts";
import { deleteAppointmentGroup, DeleteAppointmentGroupData } from "..";

export default tool({
  description: `
  Delete an appointment group
Delete an appointment group (and associated time slots and
reservations)
and return the deleted group
    `,
  parameters: deleteAppointmentGroupDataSchema.omit({ url: true }),
  execute: async (args : Omit<DeleteAppointmentGroupData, "url"> ) => {
    try {
      const { data } = await deleteAppointmentGroup(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    