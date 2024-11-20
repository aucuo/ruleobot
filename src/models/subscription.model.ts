export class Subscription {
    type: "lite" | "extended" | "pro";
    maxGroups: number;

    constructor(type: "lite" | "extended" | "pro", maxGroups: number) {
        this.type = type;
        this.maxGroups = maxGroups;
    }

    // Метод для преобразования в чистый объект
    toPlainObject(): Record<string, any> {
        return {
            type: this.type,
            maxGroups: this.maxGroups,
        };
    }
}

export const subscriptions: Record<string, Subscription> = {
    lite: new Subscription("lite", 1),
    extended: new Subscription("extended", 3),
    pro: new Subscription("pro", 7),
};
