
import { tool } from "ai";
import { getNextAppointmentDataSchema } from "./aitm.schema.ts";
import { getNextAppointment, GetNextAppointmentData } from "..";

export default tool({
  description: `
  Get next appointment
Return the next appointment available to sign up for. The appointment
is
returned in a one-element array. If no future appointments are
available, an empty array is
returned.
    `,
  parameters: getNextAppointmentDataSchema.omit({ url: true }),
  execute: async (args : Omit<GetNextAppointmentData, "url"> ) => {
    try {
      const { data } = await getNextAppointment(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    