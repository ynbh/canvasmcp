
import { tool } from "ai";
import { reserveTimeSlotParticipantIdDataSchema } from "./aitm.schema.ts";
import { reserveTimeSlotParticipantId, ReserveTimeSlotParticipantIdData } from "..";

export default tool({
  description: `
  Reserve a time slot
Reserves a particular time slot and return the new reservation
    `,
  parameters: reserveTimeSlotParticipantIdDataSchema.omit({ url: true }),
  execute: async (args : Omit<ReserveTimeSlotParticipantIdData, "url"> ) => {
    try {
      const { data } = await reserveTimeSlotParticipantId(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    