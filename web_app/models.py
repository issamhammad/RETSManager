from django.db import models

#Django Models are created to match the DDF design which is described under:
#https://www.crea.ca/wp-content/uploads/2016/02/Data_Distribution_Facility_Data_Feed_Technical_Documentation.pdf

#For details on Django Models please check:
#https://docs.djangoproject.com/en/1.9/topics/db/models/

class Property(models.Model):
    DDF_ID = 	  models.TextField(blank=True, null=True,unique=True, default=None)
    ListingType=  models.TextField(default='DDF')
    CreationDate = models.TextField(blank=True)
    LastUpdated = 	  models.TextField()
    ListingID = 	  models.TextField()
    Link= models.TextField(blank=True)
    FullAddress = models.TextField(blank=True,null=True)
    UnitNumber=models.TextField(blank=True,null=True)
    StreetNumber=models.TextField(blank=True,null=True)
    StreetName=models.TextField(blank=True,null=True)
    PostalCode = models.TextField(blank=True,null=True)
    Type = models.TextField(blank=True)
    Multi = models.BooleanField(default=False)
    Status= models.TextField(blank=True,null=True,default="active")
    NextImgId = models.IntegerField(default=1)
    ExpiryDate = models.DateTimeField(blank=True, null=True)
    ReminderCount = models.IntegerField(default=0)

#Room is shared with DDF
class Room(models.Model):
    Type= models.TextField(blank=True)
    Width= models.TextField(blank=True)
    Length= models.TextField(blank=True)
    Level= models.TextField(blank=True)
    Dimension= models.TextField(blank=True)
    Property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name="Room",null=True)

class PropertyInfo(models.Model):
    DDF_ID = 	  models.TextField(blank=True, null=True,unique=True, default=None)
    ListingType=  models.TextField(default='DDF')
    CreationDate = models.TextField(blank=True) #Doesn't exist in DDF
    LastUpdated = 	  models.TextField(blank=True)
    ListingID = 	  models.TextField()
    Board = 	  models.TextField(blank=True)
    AdditionalInformationIndicator = 	  models.TextField(blank=True)
    AmmenitiesNearBy = 	  models.TextField(blank=True)
    CommunicationType = 	  models.TextField(blank=True)
    CommunityFeatures = 	  models.TextField(blank=True)
    Crop = 	  models.TextField(blank=True)
    DocumentType = 	  models.TextField(blank=True)
    Easement = 	  models.TextField(blank=True)
    EquipmentType = 	  models.TextField(blank=True)
    Features = 	  models.TextField(blank=True)
    FarmType = 	  models.TextField(blank=True)
    IrrigationType = 	  models.TextField(blank=True)
    Lease = 	  models.TextField(blank=True)
    LeasePerTime = 	  models.TextField(blank=True)
    LeasePerUnit = 	  models.TextField(blank=True)
    LeaseTermRemainingFreq = 	  models.TextField(blank=True)
    LeaseTermRemaining = 	  models.TextField(blank=True)
    LeaseType = 	  models.TextField(blank=True)
    ListingContractDate = models.TextField(blank=True)
    LiveStockType = 	  models.TextField(blank=True)
    LoadingType = 	  models.TextField(blank=True)
    LocationDescription = 	  models.TextField(blank=True)
    Machinery = 	  models.TextField(blank=True)
    MaintenanceFee = 	  models.TextField(blank=True)
    MaintenanceFeePaymentUnit = 	  models.TextField(blank=True)
    MaintenanceFeeType = 	  models.TextField(blank=True)
    ManagementCompany = 	  models.TextField(blank=True)
    MoreInformationLink = models.TextField(blank=True)
    MunicipalId = 	  models.TextField(blank=True)
    OwnershipType = 	  models.TextField(blank=True)
    ParkingSpaceTotal = 	  models.TextField(blank=True)
    Plan = 	  models.TextField(blank=True)
    PoolFeatures = 	  models.TextField(blank=True)
    PoolType = 	  models.TextField(blank=True)
    Price = 	  models.TextField(blank=True)
    PricePerUnit = 	  models.TextField(blank=True)
    PropertyType = 	  models.TextField(blank=True)
    PublicRemarks = 	  models.TextField(blank=True)
    RentalEquipmentType = 	  models.TextField(blank=True)
    RightType = 	  models.TextField(blank=True)
    RoadType = 	  models.TextField(blank=True)
    SignType = 	  models.TextField(blank=True)
    StorageType = 	  models.TextField(blank=True)
    Structure = 	  models.TextField(blank=True)
    TransactionType = 	  models.TextField(blank=True)
    TotalBuildings = 	  models.TextField(blank=True)
    ViewType = 	  models.TextField(blank=True)
    WaterFrontType = 	  models.TextField(blank=True)
    WaterFrontName = 	  models.TextField(blank=True)
    ZoningDescription = 	  models.TextField(blank=True)
    ZoningType = 	  models.TextField(blank=True)
    Property = models.OneToOneField(Property, on_delete=models.CASCADE, related_name='Info')


class Building(models.Model):
    BathroomTotal = models.SmallIntegerField(null=True)
    BedroomsTotal = models.SmallIntegerField(null=True)
    BedroomsAboveGround = models.SmallIntegerField(null=True)
    BedroomsBelowGround = models.SmallIntegerField(null=True)
    Amenities = models.TextField(blank=True)
    Amperage = models.TextField(blank=True)
    Anchor = models.TextField(blank=True)
    Appliances = models.TextField(blank=True)
    ArchitecturalStyle = models.TextField(blank=True)
    BasementDevelopment = models.TextField(blank=True)
    BasementFeatures = models.TextField(blank=True)
    BasementType = models.TextField(blank=True)
    BomaRating = models.TextField(blank=True)
    CeilingHeight = models.TextField(blank=True)
    CeilingType = models.TextField(blank=True)
    ClearCeilingHeight = models.TextField(blank=True)
    ConstructedDate = models.TextField(blank=True)
    ConstructionMaterial = models.TextField(blank=True)
    ConstructionStatus = models.TextField(blank=True)
    ConstructionStyleAttachment = models.TextField(blank=True)
    ConstructionStyleOther = models.TextField(blank=True)
    ConstructionStyleSplitLevel = models.TextField(blank=True)
    CoolingType = models.TextField(blank=True)
    EnerguideRating = models.TextField(blank=True)
    ExteriorFinish = models.TextField(blank=True)
    FireplaceFuel = models.TextField(blank=True)
    FireplacePresent = models.TextField(blank=True)
    FireplaceTotal = models.TextField(blank=True)
    FireplaceType = models.TextField(blank=True)
    FireProtection = models.TextField(blank=True)
    Fixture = models.TextField(blank=True)
    FlooringType = models.TextField(blank=True)
    FoundationType = models.TextField(blank=True)
    HalfBathTotal = models.TextField(blank=True)
    HeatingFuel = models.TextField(blank=True)
    HeatingType = models.TextField(blank=True)
    LeedsCategory = models.TextField(blank=True)
    LeedsRating = models.TextField(blank=True)
    RoofMaterial = models.TextField(blank=True)
    RoofStyle = models.TextField(blank=True)
    SizeExterior = models.TextField(blank=True)
    SizeInterior = models.TextField(blank=True)
    StoreFront = models.TextField(blank=True)
    StoriesTotal = models.TextField(blank=True)
    TotalFinishedArea = models.TextField(blank=True)
    Type = models.TextField(blank=True)
    Uffi = models.TextField(blank=True)
    UtilityPower = models.TextField(blank=True)
    UtilityWater = models.TextField(blank=True)
    VacancyRate = models.TextField(blank=True)
    Property = models.OneToOneField(Property, on_delete=models.CASCADE, related_name='Building')


class AlternateURL(models.Model):
    BrochureLink= 	  models.TextField(blank=True)
    MapLink= 	  models.TextField(blank=True)
    PhotoLink= 	  models.TextField(blank=True)
    SoundLink= 	  models.TextField(blank=True)
    VideoLink= 	  models.TextField(blank=True)
    Property = models.OneToOneField(Property, on_delete=models.CASCADE)


class Business(models.Model):
    BusinessType= 	  models.TextField(blank=True)
    BusinessSubType= 	  models.TextField(blank=True)
    EstablishedDate= 	  models.TextField(blank=True)
    Franchise= 	  models.TextField(blank=True)
    Name= 	  models.TextField(blank=True)
    OperatingSince= 	  models.TextField(blank=True)
    Property = models.ForeignKey(Property, on_delete=models.CASCADE)


class Event(models.Model):
    Event = models.TextField(blank=True)
    StartDateTime = models.TextField(blank=True)
    EndDateTime = models.TextField(blank=True)
    Comments = models.TextField(blank=True)
    Property = models.ForeignKey(Property, on_delete=models.CASCADE)


class AgentDetails(models.Model):
    DDF_ID = models.TextField(blank=True, null=True, default=None)
    Name = models.TextField(blank=True)
    LastUpdated = models.TextField(blank=True)
    Position = models.TextField(blank=True)
    Property = models.ForeignKey(Property, on_delete=models.CASCADE,null=True, related_name="Agent")


class OfficeDetails(models.Model):
    DDF_ID = models.TextField(blank=True, null=True, default=None)
    Name = models.TextField(blank=True)
    LastUpdated = models.TextField(blank=True)
    LogoLastUpdated = models.TextField(blank=True)
    OrganizationType = models.TextField(blank=True)
    Designation = models.TextField(blank=True)
    Franchisor = models.TextField(blank=True)
    Agent = models.OneToOneField(AgentDetails, on_delete=models.CASCADE,null=True, related_name="Office")


class Address(models.Model):
    StreetAddress = models.TextField(blank=True)
    AddressLine1 = models.TextField(blank=True)
    AddressLine2 = models.TextField(blank=True)
    StreetNumber = models.TextField(blank=True)
    StreetDirectionPrefix = models.TextField(blank=True)
    StreetName = models.TextField(blank=True)
    StreetSuffix = models.TextField(blank=True)
    StreetDirectionSuffix = models.TextField(blank=True)
    UnitNumber = models.TextField(blank=True)
    BoxNumber = models.TextField(blank=True)
    City = models.TextField(blank=True)
    Province = models.TextField(blank=True)
    PostalCode = models.TextField(blank=True)
    Country = models.TextField(blank=True)
    AdditionalStreetInfo = models.TextField(blank=True)
    CommunityName = models.TextField(blank=True)
    Neighbourhood = models.TextField(blank=True)
    Subdivision = models.TextField(blank=True)
    Agent = models.OneToOneField(AgentDetails, on_delete=models.CASCADE, null=True, default=None, related_name='Address')
    Property = models.OneToOneField(Property, on_delete=models.CASCADE, null=True, default=None, related_name='Address')
    Office = models.OneToOneField(OfficeDetails, on_delete=models.CASCADE, null=True, default=None, related_name='Address')


class Phone(models.Model):
    text = models.TextField(blank=True)
    ContactType = models.TextField(blank=True)
    PhoneType = models.TextField(blank=True)
    Agent = models.ForeignKey(AgentDetails, on_delete=models.CASCADE, null=True, default=None, related_name="Phone")
    Office = models.ForeignKey(OfficeDetails, on_delete=models.CASCADE, null=True, default=None, related_name="Phone")


class Website(models.Model):
    text = models.TextField(blank=True)
    ContactType = models.TextField(blank=True)
    WebsiteType = models.TextField(blank=True)
    Agent = models.ForeignKey(AgentDetails, on_delete=models.CASCADE, null=True, default=None)
    Office = models.ForeignKey(OfficeDetails, on_delete=models.CASCADE, null=True, default=None)


class PropertyPhoto(models.Model):
    SequenceId = 	  models.SmallIntegerField()
    LastUpdated = 	  models.TextField(blank=True)
    Description = 	  models.TextField(blank=True)
    Property =        models.ForeignKey(Property, on_delete=models.CASCADE, related_name='Photos')


class Land(models.Model):
    SizeTotal= 	  models.TextField(blank=True)
    SizeTotalText= 	  models.TextField(blank=True)
    SizeFrontage= 	  models.TextField(blank=True)
    AccessType= 	  models.TextField(blank=True)
    Acreage= 	  models.TextField(blank=True)
    Amenities= 	  models.TextField(blank=True)
    ClearedTotal= 	  models.TextField(blank=True)
    CurrentUse= 	  models.TextField(blank=True)
    Divisible= 	  models.TextField(blank=True)
    FenceTotal= 	  models.TextField(blank=True)
    FenceType= 	  models.TextField(blank=True)
    FrontsOn= 	  models.TextField(blank=True)
    LandDisposition= 	  models.TextField(blank=True)
    LandscapeFeatures= 	  models.TextField(blank=True)
    PastureTotal= 	  models.TextField(blank=True)
    Sewer = 	  models.TextField(blank=True)
    SizeDepth= 	  models.TextField(blank=True)
    SoilEvaluation= 	  models.TextField(blank=True)
    SoilType= 	  models.TextField(blank=True)
    SurfaceWater= 	  models.TextField(blank=True)
    TiledTotal= 	  models.TextField(blank=True)
    Property = models.OneToOneField(Property, on_delete=models.CASCADE)


class Parking(models.Model):
    Name=models.TextField()
    Spaces=models.TextField()
    Property = models.ForeignKey(Property, on_delete=models.CASCADE,related_name="Parking")


class Utility(models.Model):
    Type= 	  models.TextField(blank=True)
    Description= 	  models.TextField(blank=True)
    Property = models.ForeignKey(Property, on_delete=models.CASCADE)


class Failed_Photos_Redownloads(models.Model):
    DDF_ID = models.TextField(blank=True)
    Photo_ID = models.TextField(blank=True)


class Geolocation(models.Model):
    lng = models.DecimalField(max_digits=17,decimal_places=14, blank=True)
    lat = models.DecimalField(max_digits=17,decimal_places=14, blank=True)
    Property = models.OneToOneField(Property, on_delete=models.CASCADE,related_name="Geo")


class DDF_LastUpdate(models.Model):
    LastUpdate = models.TextField(default="2012-08-08T21:54:28Z")
    UpdateType = models.TextField(unique=True,default="DDF")


# class AgentSpecialities(models.Model):
#     Specialty = models.TextField(blank=True)
#     Agent = models.ForeignKey(AgentDetails, on_delete=models.CASCADE)

# class AgentDesignations(models.Model):
#     Designation = models.TextField(blank=True)
#     Agent = models.ForeignKey(AgentDetails, on_delete=models.CASCADE)
#
# class AgentLanguages(models.Model):
#     Language = models.TextField(blank=True)
#     Agent = models.ForeignKey(AgentDetails, on_delete=models.CASCADE)
#
# class AgentTradingAreas(models.Model):
#     TradingArea = models.TextField(blank=True)
#     Agent = models.ForeignKey(AgentDetails, on_delete=models.CASCADE)
