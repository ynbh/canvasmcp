
import { tool } from "ai";
import { listAppointmentGroupsDataSchema } from "./aitm.schema.ts";
import { listAppointmentGroups, ListAppointmentGroupsData } from "..";

export default tool({
  description: `
  List appointment groups
Retrieve the paginated list of appointment groups that can be reserved
or
managed by the current user.
    `,
  parameters: listAppointmentGroupsDataSchema.omit({ url: true }),
  execute: async (args : Omit<ListAppointmentGroupsData, "url"> ) => {
    try {
      const { data } = await listAppointmentGroups(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    