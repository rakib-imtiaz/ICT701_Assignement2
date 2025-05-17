
import datetime
import random
import sys
import os
import time

members = []
trainers = []
class_sessions = []
transactions = []
progress_logs = []

MEMBERSHIP_PRICES = {
    "basic": 30,
    "premium": 50,
    "vip": 100
}

class member:
    def __init__(self, member_id, name, age=25, membership_type="basic", goals="get fit"):
        self.member_id = member_id
        self.name = name
        self.age = age
        self.membership_type = membership_type
        self.fitness_goals = goals
        self.class_bookings = []
        self.progress_data = []
        print(f"Added member {name}!!! :) They want to {goals}!")
    
    def update_membership(self, new_type):
        old_type = self.membership_type
        self.membership_type = new_type
        print(f"WOW! {self.name} changed from {old_type} to {new_type} membership!!!")
        return True
    
    def book_class(self, class_obj):
        if class_obj in self.class_bookings:
            print(f"HEY! {self.name} already signed up for this class!!!")
            return False
        
        if class_obj.current_enrollments >= int(class_obj.capacity):
            print(f"SO SAD :( Class {class_obj.name} is full!!")
            return False
            
        self.class_bookings.append(class_obj)
        class_obj.enroll_member(self)
        print(f"WOOHOO! {self.name} signed up for {class_obj.name}!!! :D")
        return True
    
    def track_progress(self, weight, cardio_time, strength_level):
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        progress = {
            "date": today,
            "weight": weight,
            "cardio_time": cardio_time,
            "strength": strength_level,
            "timestamp": datetime.datetime.now()
        }
        self.progress_data.append(progress)
        
        progress_logs.append({
            "member_id": self.member_id,
            "name": self.name,
            "data": progress
        })
        
        print(f"Progress logged for {self.name}!! Keep it up!!")
        return True
        
    def view_progress(self):
        if not self.progress_data:
            print(f"{self.name} hasn't logged any progress yet :(")
            return False
            
        print(f"\n*** {self.name}'s FITNESS JOURNEY ***")
        for p in self.progress_data:
            print(f"Date: {p['date']} | Weight: {p['weight']}kg | Cardio: {p['cardio_time']}min | Strength: {p['strength']}/10")
        
        if len(self.progress_data) > 1:
            first = self.progress_data[0]
            last = self.progress_data[-1]
            weight_change = float(last['weight']) - float(first['weight'])
            cardio_change = float(last['cardio_time']) - float(first['cardio_time'])
            strength_change = float(last['strength']) - float(first['strength'])
            
            print("\n=== RESULTS SO FAR ===")
            if weight_change < 0:
                print(f"Lost {abs(weight_change):.1f}kg! Amazing!!")
            else:
                print(f"Gained {weight_change:.1f}kg of muscle!! (i hope lol)")
                
            if cardio_change > 0:
                print(f"Cardio endurance up by {cardio_change:.1f} minutes!!")
            
            if strength_change > 0:
                print(f"Strength level increased by {strength_change:.1f} points!!")
                
        return True

class Trainer:
    def __init__(self, id, name, specialization="General Fitness"):
        self.id = id
        self.name = name
        self.specialization = specialization
        self.assigned_classes = []
        print(f"New trainer {name} woohoo! They specialize in {specialization}!")
    
    def assign_class(self, class_obj):
        if class_obj in self.assigned_classes:
            print(f"{self.name} is already teaching this class, silly!")
            return False
            
        self.assigned_classes.append(class_obj)
        if class_obj.trainer != self:
            class_obj.trainer = self
            
        print(f"{self.name} will teach {class_obj.name} now!! Hope they're good!")
        return True
        
    def view_schedule(self):
        if not self.assigned_classes:
            print(f"{self.name} isn't teaching any classes yet!")
            return
            
        print(f"\n*** {self.name}'s TEACHING SCHEDULE ***")
        print(f"Specialization: {self.specialization}")
        print("-" * 30)
        
        for cls in self.assigned_classes:
            print(f"Class: {cls.name} | Time: {cls.date_time} | Students: {cls.current_enrollments}/{cls.capacity}")
        
        total = len(self.assigned_classes)
        print(f"\nTotal classes: {total}")

class FitnessClass:
    def __init__(self, class_id, name, trainer, date_time, capacity):
        self.class_id = class_id
        self.name = name
        self.trainer = trainer
        self.date_time = date_time
        self.capacity = capacity
        self.current_enrollments = 0
        self.enrolled_members = []
        print(f"Made class {name} (ID: {class_id}) with trainer {trainer.name}!!")
        
        if self not in trainer.assigned_classes:
            trainer.assigned_classes.append(self)
    
    def enroll_member(self, member):
        if member in self.enrolled_members:
            print(f"{member.name} already in this class!")
            return False
            
        if self.current_enrollments >= int(self.capacity):
            print(f"Class {self.name} is FULL!!")
            return False
            
        self.enrolled_members.append(member)
        self.current_enrollments += 1
        
        if self not in member.class_bookings:
            member.class_bookings.append(self)
            
        print(f"Added {member.name} to {self.name}! That's {self.current_enrollments} people now!")
        return True
        
    def cancel_booking(self, member):
        if member not in self.enrolled_members:
            print(f"{member.name} isn't even in this class!")
            return False
            
        self.enrolled_members.remove(member)
        self.current_enrollments -= 1
        
        if self in member.class_bookings:
            member.class_bookings.remove(self)
            
        print(f"Removed {member.name} from {self.name} class. Bye bye!")
        return True

class transaction:
    def __init__(self, trans_id, member, amount, service_type="Membership"):
        self.trans_id = trans_id  
        self.member = member
        self.amount = amount
        self.service_type = service_type
        self.payment_date = datetime.datetime.now()
        print(f"Ka-ching! ${amount} from {member.name} for {service_type} :D")
    
    def process_payment(self, amount=None, service=None):
        if amount:
            self.amount = amount
        if service:
            self.service_type = service
            
        print(f"Processing ${self.amount} from {self.member.name}...")
        time.sleep(0.5)
        print("Payment successful!!")
        return True
        
    def generate_receipt(self):
        print("\n" + "=" * 30)
        print("        RECEIPT        ")
        print("=" * 30)
        print(f"Transaction #: {self.trans_id}")
        print(f"Date: {self.payment_date.strftime('%Y-%m-%d %H:%M')}")
        print(f"Member: {self.member.name} (ID: {self.member.member_id})")
        print(f"Service: {self.service_type}")
        print(f"Amount: ${self.amount}")
        print("-" * 30)
        print("Thank you for your business!")
        print("=" * 30)
        return True

def load_data():
    global members, trainers, class_sessions, transactions

    try:
        f = open('members.txt', 'r')
        for line in f:
            if line.strip() == '': 
                continue
            parts = line.strip().split(',')
            if len(parts) >= 5:
                m = member(parts[0], parts[1], parts[2], parts[3], parts[4])
            else:
                m = member(parts[0], parts[1])
            members.append(m)
        f.close()
    except Exception as e:
        print(f"Ugh, couldn't load members: {e}")

    try:
        f2 = open('trainers.txt', 'r')
        for line in f2:
            p = line.strip().split(',')
            if len(p) >= 3:
                t = Trainer(p[0], p[1], p[2])
            else:
                t = Trainer(p[0], p[1])
            trainers.append(t)
        f2.close()
    except:
        print("No trainers file found :(")
    
def save_data():
    try:
        f = open('members.txt', 'w')
        for m in members:
            f.write(f"{m.member_id},{m.name},{m.age},{m.membership_type},{m.fitness_goals}\n")
        f.close()
    except Exception as e:
        print(f"Oh no! Couldn't save members: {e}")
    
    try:
        tfile = open('trainers.txt', 'w')
        for tr in trainers:
            tfile.write(f"{tr.id},{tr.name},{tr.specialization}\n")
        tfile.close()
    except:
        print("Failed to save trainers :(((")
   

def add_member():
    print("\n+++ ADD MEMBER +++")
    mid = input("ID number: ")
    name = input("Name: ")
    age = input("Age: ")
    goals = input("Fitness goals: ")
    
    print("\nMembership types:")
    print("1. Basic ($30/month)")
    print("2. Premium ($50/month)")
    print("3. VIP ($100/month)")
    choice = input("Select membership (1-3): ")
    
    if choice == "1":
        membership = "basic"
    elif choice == "2":
        membership = "premium"
    elif choice == "3":
        membership = "vip"
    else:
        print("Invalid choice, setting to basic!")
        membership = "basic"
    
    for m in members:
        if m.member_id == mid:
            print(f"WHOOPS! ID {mid} is taken already!")
            return
    
    new_mem = member(mid, name, age, membership, goals)
    members.append(new_mem)
    
    amount = MEMBERSHIP_PRICES[membership]
    t_id = f"T{len(transactions)+1:03d}"
    trans = transaction(t_id, new_mem, amount, f"{membership.title()} Membership")
    transactions.append(trans)
    
    print(f"Yay! Added {name} to our gym :)")
    print(f"They signed up for {membership} membership at ${amount}/month")


def view_members():
    if not members:
        print("No members yet... :(")
        return
        
    print("\n*** MEMBERS ***")
    print("ID\tName\t\tAge\tMembership\tGoals")
    print("-" * 60)
    for m in members:
        name_display = m.name
        if len(name_display) < 8:
            name_display += "\t"
        
        print(f"{m.member_id}\t{name_display}\t{m.age}\t{m.membership_type}\t\t{m.fitness_goals}")
    
    total = len(members)
    
    basic = premium = vip = 0
    for m in members:
        if m.membership_type == "basic":
            basic += 1
        elif m.membership_type == "premium":
            premium += 1
        elif m.membership_type == "vip":
            vip += 1
            
    print(f"\nWe have {total} members! Wow!")
    print(f"Basic: {basic} | Premium: {premium} | VIP: {vip}")


def add_trainer():
    print("\n+++ ADD TRAINER +++")
    tid = input("Trainer ID: ")
    name = input("Name: ")
    
    print("\nSpecializations:")
    print("1. Yoga")
    print("2. Strength Training")
    print("3. Cardio")
    print("4. HIIT")
    print("5. Other")
    choice = input("Select specialization (1-5): ")
    
    if choice == "1":
        spec = "Yoga"
    elif choice == "2":
        spec = "Strength Training"
    elif choice == "3":
        spec = "Cardio"
    elif choice == "4":
        spec = "HIIT"
    elif choice == "5":
        spec = input("Enter specialization: ")
    else:
        print("Invalid choice, setting to General Fitness!")
        spec = "General Fitness"

    tr = Trainer(tid, name, spec)
    trainers.append(tr)
    print(f"Added trainer {name}!! They better be good!")


def view_trainers():
    if len(trainers) == 0:
        print("No trainers found!")
        return
        
    print("\n*** OUR AWESOME TRAINERS ***")
    print("ID\tName\t\tSpecialization")
    print("-" * 40)
    for t in trainers:
        name_display = t.name
        if len(name_display) < 8:
            name_display += "\t"
            
        print(f"{t.id}\t{name_display}\t{t.specialization}")
    
    print(f"\nTotal trainers: {len(trainers)}")


def add_class_session():
    print("\n+++ NEW CLASS +++")
    cid = input("Class ID: ")
    name = input("Class name: ")
    t_id = input("Trainer ID: ")
    
    tr_obj = None
    for tr in trainers:
        if tr.id == t_id:
            tr_obj = tr
            break
            
    if not tr_obj:
        print("TRAINER NOT FOUND!! Check ID and try again!")
        return
        
    date_time = input("When is it? (YYYY-MM-DD HH:MM): ")
    capacity = input("How many people can join?: ")
    
    sess = FitnessClass(cid, name, tr_obj, date_time, capacity)
    class_sessions.append(sess)
    print(f"Class {name} created with {tr_obj.name}!!")


def view_class_sessions():
    if not class_sessions:
        print("No classes yet... maybe add some??")
        return
        
    print("\n*** CLASS SCHEDULE ***")
    print("ID\tName\t\tTrainer\t\tTime\t\t\tCapacity")
    print("-" * 70)
    for cs in class_sessions:
        name_display = cs.name
        if len(name_display) < 8:
            name_display += "\t"
            
        trainer_display = cs.trainer.name
        if len(trainer_display) < 8:
            trainer_display += "\t"
            
        print(f"{cs.class_id}\t{name_display}\t{trainer_display}\t{cs.date_time}\t{cs.current_enrollments}/{cs.capacity}")


def book_class_for_member():
    print("\n+++ BOOK A CLASS +++")
    mid = input("Member ID: ")
    
    mem_obj = None
    for m in members:
        if m.member_id == mid:
            mem_obj = m
            break
            
    if not mem_obj:
        print(f"Can't find member {mid}! Did you type it wrong???")
        return
        
    print("\nAvailable Classes:")
    print("ID\tName\t\tTrainer\t\tTime\t\t\tAvailable")
    print("-" * 70)
    
    available_classes = []
    i = 1
    for cs in class_sessions:
        if int(cs.current_enrollments) < int(cs.capacity):
            available_classes.append(cs)
            
            name_display = cs.name
            if len(name_display) < 8:
                name_display += "\t"
                
            trainer_display = cs.trainer.name
            if len(trainer_display) < 8:
                trainer_display += "\t"
                
            print(f"{i}. {cs.class_id}\t{name_display}\t{trainer_display}\t{cs.date_time}\t{int(cs.capacity) - int(cs.current_enrollments)} spots")
            i += 1
    
    if not available_classes:
        print("No classes available right now :(")
        return
        
    choice = input("Select class number: ")
    try:
        idx = int(choice) - 1
        if idx < 0 or idx >= len(available_classes):
            print("Invalid choice!")
            return
            
        selected_class = available_classes[idx]
        mem_obj.book_class(selected_class)
        
        if mem_obj.membership_type == "basic":
            t_id = f"T{len(transactions)+1:03d}"
            trans = transaction(t_id, mem_obj, "10", f"Class: {selected_class.name}")
            transactions.append(trans)
            print(f"Charged ${10} for the class!")
        else:
            print(f"No charge for {mem_obj.membership_type} members! Classes included! :D")
            
    except ValueError:
        print("Please enter a number!")
        return


def add_transaction():
    print("\n+++ NEW PAYMENT +++")
    tid = input("Transaction ID: ")
    mid = input("Member ID: ")
    
    mem_obj = None
    for m in members:
        if m.member_id == mid:
            mem_obj = m
            break
            
    if not mem_obj:
        print(f"Can't find member {mid}! Did you type it wrong???")
        return
        
    print("\nPayment type:")
    print("1. Membership renewal")
    print("2. Class payment")
    print("3. Personal training")
    print("4. Other")
    choice = input("Select payment type (1-4): ")
    
    if choice == "1":
        service = f"{mem_obj.membership_type.title()} Membership Renewal"
        amount = MEMBERSHIP_PRICES[mem_obj.membership_type]
    elif choice == "2":
        service = "Class Payment"
        amount = "10"
    elif choice == "3":
        service = "Personal Training"
        amount = "50"
    elif choice == "4":
        service = input("Enter service description: ")
        amount = input("Enter amount: $")
    else:
        print("Invalid choice, setting to Other Payment")
        service = "Other Payment"
        amount = input("Enter amount: $")
    
    tran = transaction(tid, mem_obj, amount, service)
    tran.process_payment()
    transactions.append(tran)
    
    tran.generate_receipt()
    
    print(f"Got ${amount} from {mem_obj.name}! Cha-ching!")


def view_transactions():
    if not transactions:
        print("No money yet :(")
        return
        
    print("\n*** MONEY STUFF ***")
    print("ID\tMember\t\tService\t\t\t\tAmount")
    print("-" * 70)
    total = 0
    
    for tr in transactions:
        name_display = tr.member.name
        if len(name_display) < 8:
            name_display += "\t"
            
        service_display = tr.service_type
        if len(service_display) < 16:
            service_display += "\t\t"
        elif len(service_display) < 24:
            service_display += "\t"
            
        print(f"{tr.trans_id}\t{name_display}\t{service_display}\t${tr.amount}")
        
        try:
            total += float(tr.amount)
        except:
            print(f"WARNING: {tr.amount} isn't a valid number! Fix this!")
            
    print(f"\nTotal money: ${total:.2f} woohoo!")


def track_member_progress():
    print("\n+++ TRACK FITNESS PROGRESS +++")
    mid = input("Member ID: ")
    
    mem_obj = None
    for m in members:
        if m.member_id == mid:
            mem_obj = m
            break
            
    if not mem_obj:
        print(f"Can't find member {mid}! Did you type it wrong???")
        return
    
    print(f"Tracking progress for {mem_obj.name}!")
    print(f"Goal: {mem_obj.fitness_goals}")
    
    try:
        weight = input("Current weight (kg): ")
        cardio = input("Cardio endurance (minutes): ")
        strength = input("Strength level (1-10): ")
        
        mem_obj.track_progress(weight, cardio, strength)
        
    except ValueError:
        print("Please enter valid numbers!")
        return


def view_member_progress():
    print("\n+++ VIEW PROGRESS +++")
    mid = input("Member ID: ")
    
    mem_obj = None
    for m in members:
        if m.member_id == mid:
            mem_obj = m
            break
            
    if not mem_obj:
        print(f"Can't find member {mid}! Did you type it wrong???")
        return
        
    mem_obj.view_progress()


def generate_revenue_report():
    print("\n+++ REVENUE REPORT +++")
    if not transactions:
        print("No transactions yet!")
        return
        
    total_revenue = 0
    membership_revenue = 0
    class_revenue = 0
    training_revenue = 0
    other_revenue = 0
    
    for t in transactions:
        try:
            amount = float(t.amount)
            total_revenue += amount
            
            if "membership" in t.service_type.lower():
                membership_revenue += amount
            elif "class" in t.service_type.lower():
                class_revenue += amount
            elif "training" in t.service_type.lower():
                training_revenue += amount
            else:
                other_revenue += amount
                
        except ValueError:
            print(f"Warning: Invalid amount in transaction {t.trans_id}")
    
    class_counts = {}
    for c in class_sessions:
        class_counts[c.name] = c.current_enrollments
        
    top_class = None
    top_count = 0
    for name, count in class_counts.items():
        if int(count) > top_count:
            top_count = int(count)
            top_class = name
    
    active_count = 0
    today = datetime.datetime.now()
    thirty_days_ago = today - datetime.timedelta(days=30)
    
    active_members = set()
    for t in transactions:
        if t.payment_date > thirty_days_ago:
            active_members.add(t.member.member_id)
    
    active_count = len(active_members)
    
    print("\n" + "=" * 50)
    print("          REVENUE REPORT          ")
    print("=" * 50)
    print(f"Total Revenue: ${total_revenue:.2f}")
    print("-" * 50)
    print(f"Membership Revenue: ${membership_revenue:.2f}")
    print(f"Class Revenue: ${class_revenue:.2f}")
    print(f"Personal Training Revenue: ${training_revenue:.2f}")
    print(f"Other Revenue: ${other_revenue:.2f}")
    print("-" * 50)
    
    if top_class:
        print(f"Most Popular Class: {top_class} ({top_count} members)")
    else:
        print("No classes have been booked yet")
        
    print(f"Active Members: {active_count}")
    print(f"Total Members: {len(members)}")
    print("=" * 50)


def cancel_membership():
    print("\n+++ CANCEL MEMBERSHIP +++")
    mid = input("Member ID to cancel: ")
    
    mem_idx = -1
    for i, m in enumerate(members):
        if m.member_id == mid:
            mem_idx = i
            break
            
    if mem_idx == -1:
        print(f"Can't find member {mid}! Did you type it wrong???")
        return
        
    mem = members[mem_idx]
    print(f"Are you sure you want to cancel {mem.name}'s membership? (y/n)")
    confirm = input("> ")
    
    if confirm.lower() == "y":
        for cls in mem.class_bookings[:]:
            cls.cancel_booking(mem)
            
        cancelled_member = members.pop(mem_idx)
        print(f"Membership cancelled for {cancelled_member.name}. We'll miss you! :(")
    else:
        print("Cancellation aborted! Yay!")


def show_menu():
    print("\n======= GYM MANAGER  =======")
    print("1. Add Member")
    print("2. Show Members")
    print("3. Add Trainer")
    print("4. Show Trainers")
    print("5. Make a Class")
    print("6. Show Classes")
    print("7. Book a Class")
    print("8. Record Payment")
    print("9. Payment History")
    print("10. Track Fitness Progress")
    print("11. View Progress")
    print("12. Generate Revenue Report")
    print("13. Cancel Membership")
    print("0. Quit")
    print("=================================")

def run_tests():
    print("RUNNING TESTS!!!")
    members.clear()
    trainers.clear() 
    class_sessions.clear()
    transactions.clear()
    
    print("Testing member...")
    members.append(member("001", "Bob Smith", "30", "premium", "lose weight"))
    print("PASS" if members[0].member_id == "001" else "FAIL")
    
    print("Testing dupes...")
    dupe_id = "001"
    has_dupe = False
    for m in members:
        if m.member_id == dupe_id:
            has_dupe = True
            break
    print("PASS" if has_dupe else "FAIL")
    
    print("Making a trainer...")
    trainers.append(Trainer("T1", "Jim", "Yoga"))
    print("PASS" if trainers[0].name == "Jim" else "FAIL")
    
    print("Creating class...")
    class_sessions.append(FitnessClass("YOGA1", "Morning Yoga", trainers[0], "2023-12-01 10:00", "15"))
    print("PASS" if class_sessions[0].name == "Morning Yoga" else "FAIL")
    
    print("Testing money...")
    transactions.append(transaction("T001", members[0], "50", "Premium Membership"))
    print("PASS" if transactions[0].trans_id == "T001" else "FAIL")
    
    print("Testing class booking...")
    members[0].book_class(class_sessions[0])
    print("PASS" if members[0].class_bookings[0].name == "Morning Yoga" else "FAIL")
    
    print("Testing progress tracking...")
    members[0].track_progress("80", "30", "5")
    print("PASS" if len(members[0].progress_data) == 1 else "FAIL")
    
    print("ALL DONE!!!")

def main():
    load_data()
    
    while True:
        show_menu()
        choice = input("What do you want to do? ")
        
        if choice == "1": 
            add_member()
        elif choice == "2": 
            view_members()
        elif choice == "3": 
            add_trainer()
        elif choice == "4": 
            view_trainers()
        elif choice == "5": 
            add_class_session()
        elif choice == "6": 
            view_class_sessions()
        elif choice == "7":
            book_class_for_member()
        elif choice == "8": 
            add_transaction()
        elif choice == "9": 
            view_transactions()
        elif choice == "10":
            track_member_progress()
        elif choice == "11":
            view_member_progress()
        elif choice == "12":
            generate_revenue_report()
        elif choice == "13":
            cancel_membership()
        elif choice == "0":
            print("Bye bye! Saving your data...")
            save_data()
            print("See ya later!")
            break
        elif choice.lower() == "test":
            run_tests()
        elif choice.lower() == "help":
            print("Just pick a number from the menu, duh!")
        else:
            print("HUH? Try again with a valid option!")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nHey! You interrupted me! Saving anyway...")
        save_data()
    except Exception as e:
        print(f"OMG SOMETHING BROKE: {e}")
        print("Trying to save...")
        try:
            save_data()
        except:
            print("Double fail! Couldn't save :((((")
