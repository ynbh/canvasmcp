
import { tool } from "ai";
import { reserveTimeSlotDataSchema } from "./aitm.schema.ts";
import { reserveTimeSlot, ReserveTimeSlotData } from "..";

export default tool({
  description: `
  Reserve a time slot
Reserves a particular time slot and return the new reservation
    `,
  parameters: reserveTimeSlotDataSchema.omit({ url: true }),
  execute: async (args : Omit<ReserveTimeSlotData, "url"> ) => {
    try {
      const { data } = await reserveTimeSlot(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    