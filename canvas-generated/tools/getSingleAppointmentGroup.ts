
import { tool } from "ai";
import { getSingleAppointmentGroupDataSchema } from "./aitm.schema.ts";
import { getSingleAppointmentGroup, GetSingleAppointmentGroupData } from "..";

export default tool({
  description: `
  Get a single appointment group
Returns information for a single appointment group
    `,
  parameters: getSingleAppointmentGroupDataSchema.omit({ url: true }),
  execute: async (args : Omit<GetSingleAppointmentGroupData, "url"> ) => {
    try {
      const { data } = await getSingleAppointmentGroup(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    